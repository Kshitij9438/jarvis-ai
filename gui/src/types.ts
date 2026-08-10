export type JarvisEvent = {
  type: string;
  data: Record<string, unknown>;
};

export type ChatResult = {
  step: string | null;
  success: boolean;
  result: unknown;
  error: string | null;
};

export type ChatResponse = {
  message: string;
  plan: {
    steps: Array<{
      action: string;
      args: Record<string, unknown>;
    }>;
  } | null;
  results: ChatResult[];
  context: Record<string, unknown> | null;
};

export type EventResponse = {
  response: ChatResponse;
  events: JarvisEvent[];
};