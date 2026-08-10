import type { ChatResponse, EventResponse } from "./types";

const API_URL = "http://127.0.0.1:8000";

async function request<T>(
  path: string,
  message: string,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      `JARVIS request failed (${response.status}): ${detail}`,
    );
  }

  return response.json() as Promise<T>;
}

export function sendMessage(
  message: string,
): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", message);
}

export function sendMessageWithEvents(
  message: string,
): Promise<EventResponse> {
  return request<EventResponse>("/api/chat/events", message);
}