// This file contains type definitions for your data.

import { number } from "zod";

export type Context={
  id: number;
  context_name: string;
  chunk_size: number;
  /*
  chunk_overlap:  number;
  context_size: number;
  chunk_threshold:  number;
  load_threshold: number;
  chunk_weight: number;
  load_weight: number;
  embedding_model: number;  
  context_type: number;
  history: boolean;
*/
}

export type User = {
  id: string;
  name: string;
  email: string;
  password: string;
};

