import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 40 }}>
      <h1>Library Frontend</h1>
      <p>Frontend connected structure is ready.</p>

      <Link href="/login">
      <button>Go to Login</button>
      </Link>
    </main>
  );
  }