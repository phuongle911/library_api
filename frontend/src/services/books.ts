import { apiRequest } from "@/lib/api";
import type { Book } from "@/types/book";

export async function getBooks() {
    return apiRequest<Book[]>("/api/v1/books", {
        method: "GET",
        auth: true,
    });
}