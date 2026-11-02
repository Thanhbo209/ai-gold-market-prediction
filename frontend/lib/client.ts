// Typed API client for prediction endpoints
import { api, ApiError } from "./api";
import {
  PredictionResponseSchema,
  PredictionHistoryResponseSchema,
} from "../types/api";
import type {
  PredictionResponse,
  PredictionHistoryResponse,
} from "../types/api";

/**
 * Fetch the latest prediction.
 * Returns a typed {@link PredictionResponse} or throws {@link ApiError} on HTTP error.
 * Runtime validation ensures the response matches the backend schema.
 */
export const getLatestPrediction = async (): Promise<PredictionResponse> => {
  const response = await api("/predictions/latest");
  const json = await response.json();
  const result = PredictionResponseSchema.safeParse(json);
  if (!result.success) {
    throw new ApiError(
      response.status,
      "Invalid response shape",
      result.error.message,
    );
  }
  return result.data;
};

/**
 * Fetch paginated prediction history.
 * @param params Query parameters for pagination and optional date filters.
 * Returns a typed {@link PredictionHistoryResponse}.
 */
export const getPredictionHistory = async (
  params: {
    skip?: number;
    limit?: number;
    start_date?: string; // ISO date string, e.g., "2024-01-01"
    end_date?: string;
  } = {},
): Promise<PredictionHistoryResponse> => {
  const query = new URLSearchParams();
  if (params.skip !== undefined) query.append("skip", String(params.skip));
  if (params.limit !== undefined) query.append("limit", String(params.limit));
  if (params.start_date) query.append("start_date", params.start_date);
  if (params.end_date) query.append("end_date", params.end_date);

  const response = await api(
    "/predictions" + (query.toString() ? `?${query}` : ""),
  );
  const json = await response.json();
  const result = PredictionHistoryResponseSchema.safeParse(json);
  if (!result.success) {
    throw new ApiError(
      response.status,
      "Invalid response shape",
      result.error.message,
    );
  }
  return result.data;
};
