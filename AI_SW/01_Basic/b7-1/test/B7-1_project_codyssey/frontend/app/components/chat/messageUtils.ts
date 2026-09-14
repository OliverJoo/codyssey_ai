import { ChatMessage } from "../../lib/api";

export function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

export function mergeMessages(current: ChatMessage[], incoming: ChatMessage[]) {
  const byId = new Map<string, ChatMessage>();
  [...current, ...incoming].forEach((message) => byId.set(message.id, message));
  return [...byId.values()].sort(
    (first, second) => Date.parse(first.createdAt) - Date.parse(second.createdAt),
  );
}

export function appendMessages(current: ChatMessage[], incoming: ChatMessage[]) {
  // 실시간 메시지는 브라우저와 서버의 시간대 차이에 영향받지 않도록 수신 순서대로 추가합니다.
  const messages = [...current];
  incoming.forEach((message) => {
    const existingIndex = messages.findIndex((item) => item.id === message.id);
    if (existingIndex >= 0) messages[existingIndex] = message;
    else messages.push(message);
  });
  return messages;
}

export function createUserMessage(content: string): ChatMessage {
  const createdAt = new Date();
  return {
    id: `user-${createdAt.getTime()}`,
    role: "user",
    content,
    status: "sending",
    createdAt: createdAt.toISOString(),
  };
}
