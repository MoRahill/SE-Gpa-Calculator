import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "GPA Calculator",
  description: "Calculate and predict your GPA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
