import "./globals.css";

import Footer from "@components/layout/footer";
import NavBar from "@components/layout/navbar";
import { ReactNode, Suspense } from 'react';
import {
  ClerkProvider,
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton
} from '@clerk/nextjs'

export const metadata = {
  title: "SG Property Hub",
  description: "Tìm bất động sản thông minh",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // <ClerkProvider>
    <html lang='vi'>
      <body className='relative'>
          {/* <SignedOut> */}
            {/* <SignInButton /> */}
          {/* </SignedOut> */}
          {/* <SignedIn> */}
            {/* <UserButton /> */}
          {/* </SignedIn> */}
        <NavBar/>
        <Suspense>
          {children}
        </Suspense>
        <Footer />
      </body>
    </html>
    // </ClerkProvider>
  );
}
