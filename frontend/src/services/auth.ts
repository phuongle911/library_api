import { apiRequest } from "@/lib/api";
import type { LoginRequest, LoginResponse } from "@/types/auth";

export async function loginUser(data: LoginRequest) {
  return apiRequest<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function saveToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function logoutUser() {
  localStorage.removeItem("access_token");
}
