import { Sprite } from "../common/Sprite";

export function FieldIcon({ type }: { type: "user" | "lock" }) {
  return type === "user" ? (
    <Sprite x={96} y={564} width={22} height={23} className="field-icon" />
  ) : (
    <Sprite x={96} y={644} width={22} height={23} className="field-icon" />
  );
}
