from __future__ import annotations

import json
import os
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import jmespath


PROJECT = Path(__file__).resolve().parents[1]


class WorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "b6-1"
        shutil.copytree(PROJECT, self.root, ignore=shutil.ignore_patterns(".state", "config.env", "aws-evidence-*.txt"))
        self.fake_bin = Path(self.temp.name) / "bin"
        self.fake_bin.mkdir()
        shutil.copy2(PROJECT / "tests/fake_aws.py", self.fake_bin / "aws")
        (self.fake_bin / "aws").chmod((self.fake_bin / "aws").stat().st_mode | stat.S_IXUSR)
        self._write_executable(
            "curl",
            "#!/usr/bin/env bash\n"
            "[[ \" $* \" == *\" --include \"* ]] && printf 'HTTP/1.1 200 OK\\n\\n'\n"
            "if [[ \" $* \" == *\"/health\"* ]]; then\n"
            "  printf 'OK\\n'\n"
            "else\n"
            "  printf '<html><body data-project=\"codyssey-b6-1\">Codyssey Cloud Lab</body></html>\\n'\n"
            "fi\n",
        )
        self._write_executable("ssh", "#!/usr/bin/env bash\nexit 0\n")
        self._write_executable("sleep", "#!/usr/bin/env bash\nexit 0\n")
        config = (self.root / "02_config.env.example").read_text(encoding="utf-8")
        (self.root / "config.env").write_text(config.replace("CHANGE_ME/32", "203.0.113.10/32"), encoding="utf-8")
        self.env = {
            **os.environ,
            "PATH": f"{self.fake_bin}:{os.environ['PATH']}",
            "FAKE_AWS_STATE": str(Path(self.temp.name) / "fake-aws.json"),
            "B6_VERIFY_ATTEMPTS": "1",
            "B6_VERIFY_SLEEP": "0",
            "B6_CLEANUP_ATTEMPTS": "1",
            "B6_CLEANUP_SLEEP": "0",
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_executable(self, name: str, body: str) -> None:
        path = self.fake_bin / name
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_script(self, name: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.root / name)],
            cwd=self.root,
            env=self.env,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )

    def assert_success(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_full_lifecycle_can_run_twice(self) -> None:
        for _ in range(2):
            self.assert_success(self.run_script("04_create_infrastructure.sh"))
            self.assertTrue((self.root / ".state/resources.env").exists())
            self.assert_success(self.run_script("06_verify_service.sh"))
            self.assert_success(self.run_script("07_collect_evidence.sh"))
            evidence = list((self.root / "docs/evidence").glob("aws-evidence-*.txt"))
            self.assertTrue(evidence)
            self.assert_success(self.run_script("08_cleanup_resources.sh", "DELETE\n"))
            self.assertFalse((self.root / ".state/resources.env").exists())
            self.assertFalse((self.root / ".state/key.pem").exists())
        self.assert_success(self.run_script("08_cleanup_resources.sh"))

    def test_invalid_ssh_ipv4_is_rejected(self) -> None:
        config_path = self.root / "config.env"
        config_path.write_text(config_path.read_text().replace("203.0.113.10/32", "999.0.0.1/32"))
        result = self.run_script("03_validate_prerequisites.sh")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("유효하지 않은 IPv4", result.stdout)

    def test_static_requirements(self) -> None:
        prerequisites = (self.root / "03_validate_prerequisites.sh").read_text(encoding="utf-8")
        self.assertNotIn("--max-results", prerequisites)

        architecture = (self.root / "01_architecture.html").read_text(encoding="utf-8")
        self.assertIn("PUBLIC SUBNET 10.0.1.0/24", architecture)
        user_data = (self.root / "05_user_data.sh").read_text(encoding="utf-8")
        web_page = (self.root / "web/index.html").read_text(encoding="utf-8")
        amazon_linux_install = next(
            line for line in user_data.splitlines() if line.strip().startswith("dnf install")
        )
        self.assertNotIn("curl", amazon_linux_install.split())
        self.assertNotIn("listen 80 default_server", user_data)
        self.assertIn("/usr/share/nginx/html /var/www/html", user_data)
        self.assertIn('data-project="codyssey-b6-1"', web_page)
        self.assertIn("fetch('/health'", web_page)
        create_script = (self.root / "04_create_infrastructure.sh").read_text(encoding="utf-8")
        self.assertIn('WEB_SOURCE="$SCRIPT_DIR/web/index.html"', create_script)
        verify_script = (self.root / "06_verify_service.sh").read_text(encoding="utf-8")
        self.assertIn("External GET / -> 200, authored web page", verify_script)
        policy = json.loads((self.root / "iam/least-privilege-policy.json").read_text(encoding="utf-8"))
        actions = {action for statement in policy["Statement"] for action in statement["Action"]}
        self.assertFalse({"s3:*", "rds:*", "iam:*", "AdministratorAccess"} & actions)

        answer_md = (self.root / "README_answer.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^### Q\d+\.", answer_md, re.MULTILINE)), 17)
        answer_html = (self.root / "README_answer.html").read_text(encoding="utf-8")
        self.assertEqual(answer_html.count("<h3 id="), 17)

        troubleshooting = (self.root / "docs/troubleshooting.md").read_text(encoding="utf-8")
        for heading in ("증상", "가설", "검증", "조치", "결과", "재발 방지"):
            self.assertIn(heading, troubleshooting)
        cleanup = (self.root / "docs/cleanup-checklist.md").read_text(encoding="utf-8")
        for resource in ("EC2", "EBS", "Elastic IP", "Internet Gateway", "VPC"):
            self.assertIn(resource, cleanup)

        png_header = (self.root / "docs/architecture.png").read_bytes()[:24]
        self.assertEqual(png_header[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png_header[16:24]), (2400, 1360))

    def test_aws_queries_match_expected_shapes(self) -> None:
        instances = {
            "Reservations": [{
                "Instances": [
                    {"State": {"Name": "running"}},
                    {"State": {"Name": "terminated"}},
                ]
            }]
        }
        remaining_query = "length(Reservations[].Instances[?State.Name!='terminated'][])"
        self.assertEqual(jmespath.search(remaining_query, instances), 1)

        rules = {
            "SecurityGroupRules": [
                {"IsEgress": False, "IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "CidrIpv4": "0.0.0.0/0"},
                {"IsEgress": False, "IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "CidrIpv4": "203.0.113.10/32"},
            ]
        }
        http_query = "SecurityGroupRules[?IsEgress==`false` && IpProtocol=='tcp' && FromPort==`80` && ToPort==`80`].CidrIpv4 | [0]"
        self.assertEqual(jmespath.search(http_query, rules), "0.0.0.0/0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
