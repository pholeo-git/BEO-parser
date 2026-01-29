import type { Metadata } from 'next'
import { Inter, Open_Sans, KoHo } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const openSans = Open_Sans({ 
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-open-sans'
})
const koho = KoHo({ 
  subsets: ['latin'],
  weight: ['500'],
  variable: '--font-koho'
})

export const metadata: Metadata = {
  title: 'BEO Separator - Pholeo',
  description: 'Split your BEO packet PDFs into individual BEO files',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${openSans.variable} ${koho.variable}`}>
      <body style={{ fontFamily: 'var(--font-open-sans)' }}>
        {children}
      </body>
    </html>
  )
}
