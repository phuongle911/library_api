"use client";

import { useEffect, useState } from "react";
import { getBooks } from "@/services/books";
import type { Book } from "@/types/book";

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadBooks() {
      try {
        const data = await getBooks();
        setBooks(data);
      } catch (error) {
        console.error(error);
        setError("Failed to load books.");
      } finally {
        setLoading(false);
      }
    }

    loadBooks();
  }, []);

  if (loading) return <main style={{ padding: 40 }}>Loading books...</main>;

  return (
    <main style={{ padding: 40 }}>
      <h1>Books</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {books.map((book) => (
        <div
          key={book.id}
          style={{
            border: "1px solid #ddd",
            padding: 16,
            borderRadius: 8,
            marginBottom: 12,
          }}
        >
          <h3>{book.title}</h3>
          <p>Author: {book.author || "N/A"}</p>
          <p>Available Copies: {book.available_copies ?? "N/A"}</p>
        </div>
      ))}
    </main>
  );
}
