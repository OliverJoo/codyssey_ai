#!/usr/bin/env python3
"""b6-1 셸 워크플로우를 비용 없이 통합 테스트하는 최소 AWS CLI 대역."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


STATE_PATH = Path(os.environ["FAKE_AWS_STATE"])
DEFAULT_STATE = {
    "vpc": False,
    "subnet": False,
    "igw": False,
    "igw_attached": False,
    "route_table": False,
    "route_associated": False,
    "security_group": False,
    "key_pair": False,
    "instance": False,
    "instance_state": "terminated",
    "volume": False,
}


def load_state() -> dict[str, object]:
    if STATE_PATH.exists():
        return {**DEFAULT_STATE, **json.loads(STATE_PATH.read_text())}
    return DEFAULT_STATE.copy()


def save_state(state: dict[str, object]) -> None:
    STATE_PATH.write_text(json.dumps(state), encoding="utf-8")


def option(args: list[str], name: str, default: str = "") -> str:
    try:
        return args[args.index(name) + 1]
    except (ValueError, IndexError):
        return default


def output(value: object = "") -> None:
    if isinstance(value, (dict, list)):
        print(json.dumps(value))
    elif value != "":
        print(value)


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 2:
        return 2
    service, operation = args[0], args[1]
    query = option(args, "--query")
    state = load_state()

    if service == "sts" and operation == "get-caller-identity":
        if query == "Account":
            output("123456789012")
        elif query == "Arn":
            output("arn:aws:iam::123456789012:user/codyssey-test")
        else:
            output({"Account": "123456789012", "Arn": "arn:aws:iam::123456789012:user/codyssey-test"})
        return 0

    if service == "ssm" and operation == "get-parameter":
        output("ami-test1234")
        return 0

    if service != "ec2":
        return 2

    if operation == "describe-availability-zones":
        output("ap-northeast-2a" if query else {"AvailabilityZones": [{"ZoneName": "ap-northeast-2a"}]})
    elif operation == "describe-vpcs":
        if query == "Vpcs[].VpcId":
            output("vpc-test1234" if state["vpc"] else "")
        elif query == "Vpcs[0].[State,CidrBlock]":
            output("available\t10.0.0.0/16")
        elif query == "length(Vpcs)":
            output(1 if state["vpc"] else 0)
        else:
            output({"Vpcs": []})
    elif operation == "create-vpc":
        state["vpc"] = True
        save_state(state)
        output("vpc-test1234")
    elif operation == "modify-vpc-attribute":
        pass
    elif operation == "delete-vpc":
        state["vpc"] = False
        save_state(state)
    elif operation == "describe-subnets":
        if query == "Subnets[0].[VpcId,CidrBlock,MapPublicIpOnLaunch]":
            output("vpc-test1234\t10.0.1.0/24\tTrue")
        elif query == "length(Subnets)":
            output(1 if state["subnet"] else 0)
        else:
            output({"Subnets": []})
    elif operation == "create-subnet":
        state["subnet"] = True
        save_state(state)
        output("subnet-test1234")
    elif operation == "modify-subnet-attribute":
        pass
    elif operation == "delete-subnet":
        state["subnet"] = False
        save_state(state)
    elif operation == "describe-internet-gateways":
        if query == "InternetGateways[0].Attachments[0].VpcId":
            output("vpc-test1234" if state["igw_attached"] else "None")
        elif query.startswith("length(InternetGateways[0].Attachments"):
            output(1 if state["igw_attached"] else 0)
        elif query == "length(InternetGateways)":
            output(1 if state["igw"] else 0)
        else:
            output({"InternetGateways": []})
    elif operation == "create-internet-gateway":
        state["igw"] = True
        save_state(state)
        output("igw-test1234")
    elif operation == "attach-internet-gateway":
        state["igw_attached"] = True
        save_state(state)
    elif operation == "detach-internet-gateway":
        state["igw_attached"] = False
        save_state(state)
    elif operation == "delete-internet-gateway":
        state["igw"] = False
        save_state(state)
    elif operation == "describe-route-tables":
        if "Routes[?DestinationCidrBlock" in query:
            output("igw-test1234")
        elif "Associations[?SubnetId" in query:
            output("subnet-test1234")
        elif query.startswith("length(RouteTables[0].Associations"):
            output(1 if state["route_associated"] else 0)
        elif query == "length(RouteTables)":
            output(1 if state["route_table"] else 0)
        else:
            output({"RouteTables": []})
    elif operation == "create-route-table":
        state["route_table"] = True
        save_state(state)
        output("rtb-test1234")
    elif operation == "create-route":
        output(True)
    elif operation == "associate-route-table":
        state["route_associated"] = True
        save_state(state)
        output("rtbassoc-test1234")
    elif operation == "disassociate-route-table":
        state["route_associated"] = False
        save_state(state)
    elif operation == "delete-route-table":
        state["route_table"] = False
        save_state(state)
    elif operation == "describe-security-groups":
        output(1 if query == "length(SecurityGroups)" and state["security_group"] else 0)
    elif operation == "describe-security-group-rules":
        if query.startswith("length("):
            output(2)
        elif "FromPort==`80`" in query:
            output("0.0.0.0/0")
        elif "FromPort==`22`" in query:
            output("203.0.113.10/32")
        else:
            output({"SecurityGroupRules": []})
    elif operation == "create-security-group":
        state["security_group"] = True
        save_state(state)
        output("sg-test1234")
    elif operation == "authorize-security-group-ingress":
        pass
    elif operation == "delete-security-group":
        state["security_group"] = False
        save_state(state)
    elif operation == "describe-key-pairs":
        if "--key-names" in args:
            if not state["key_pair"]:
                return 255
            output({"KeyPairs": [{"KeyName": "codyssey-b6-1-key"}]})
        elif query == "length(KeyPairs)":
            output(1 if state["key_pair"] else 0)
        else:
            output({"KeyPairs": []})
    elif operation == "create-key-pair":
        state["key_pair"] = True
        save_state(state)
        output("-----BEGIN OPENSSH PRIVATE KEY-----\nfake\n-----END OPENSSH PRIVATE KEY-----")
    elif operation == "delete-key-pair":
        state["key_pair"] = False
        save_state(state)
    elif operation == "run-instances":
        state.update(instance=True, instance_state="running", volume=True)
        save_state(state)
        output("i-test1234")
    elif operation == "describe-instances":
        if query.endswith("BlockDeviceMappings[0].Ebs.VolumeId"):
            output("vol-test1234")
        elif query.endswith("PublicIpAddress"):
            output("198.51.100.10")
        elif query.endswith("State.Name"):
            output(state["instance_state"] if state["instance"] else "None")
        elif "State.Name,InstanceType,SubnetId" in query:
            output("running\tt3.micro\tsubnet-test1234\t198.51.100.10\tsg-test1234")
        elif "BlockDeviceMappings[0].[Ebs.VolumeId" in query:
            output("vol-test1234\tTrue")
        elif query.startswith("length(Reservations"):
            count = int(bool(state["instance"] and state["instance_state"] != "terminated"))
            output(count)
        else:
            output({"Reservations": []})
    elif operation == "terminate-instances":
        state["instance_state"] = "terminated"
        state["volume"] = False
        save_state(state)
        output({"TerminatingInstances": [{"InstanceId": "i-test1234"}]})
    elif operation == "describe-volumes":
        if query == "Volumes[0].Size":
            output(8)
        elif query == "length(Volumes)":
            output(1 if state["volume"] else 0)
        else:
            output({"Volumes": []})
    elif operation == "describe-addresses":
        output(0 if query == "length(Addresses)" else {"Addresses": []})
    elif operation == "wait":
        pass
    else:
        print(f"unsupported fake aws operation: {' '.join(args)}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
