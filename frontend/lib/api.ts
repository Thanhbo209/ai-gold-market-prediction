// API base configuration
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = async (
  input: RequestInfo,
  init?: RequestInit,
): Promise<Response> => {
  const url = typeof input === "string" ? `${BASE_URL}${input}` : input;
  const response = await fetch(url, {
    ...init,
  });

  // response.ok is true when the HTTP status is between 200 and 299.
  if (!response.ok) {
    const errorBody = await response.text().catch(() => "");
    throw new ApiError(response.status, response.statusText, errorBody);
  }
  return response;
};

export class ApiError extends Error {
  public readonly status: number;
  public readonly data?: any;
  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}
