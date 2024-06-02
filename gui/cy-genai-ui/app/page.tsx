import { redirect } from 'next/navigation'
 

export default function Page() {
  return redirect('/home')
}

export const metadata = {
  title: "CyGenAI UI",
  description: "CyGenAI User Interface",
}