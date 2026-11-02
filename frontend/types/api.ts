import { z } from "zod";

export const PredictionResponseSchema = z.object({
  date: z.string(),
  data_source: z.string(),
  selected_model: z.string(),
  predicted_direction: z.union([z.literal(0), z.literal(1)]),
  predicted_label: z.string(),
});

export type PredictionResponse = z.infer<typeof PredictionResponseSchema>;

export const PredictionHistoryResponseSchema = z.object({
  items: z.array(PredictionResponseSchema),
  total: z.number().int().nonnegative(),
  skip: z.number().int().nonnegative(),
  limit: z.number().int().positive(),
});

export type PredictionHistoryResponse = z.infer<typeof PredictionHistoryResponseSchema>;
