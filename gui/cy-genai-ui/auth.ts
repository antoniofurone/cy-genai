import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { authConfig } from './auth.config';
import { z } from 'zod';
import {User} from '@/app/lib/definitions'

async function getUser(email: string): Promise<User | undefined> {
  try {
    const user:User={id:"1",name:"antonio",email:"furone.antonio@gmail.com",password:'xxxx'}
    return user
  } catch (error) {
    console.error('Failed to fetch user:', error);
    throw new Error('Failed to fetch user.');
  }
}
 
export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({

      async authorize(credentials) {
        console.log("authorize....")
        const parsedCredentials = z
          .object({ email: z.string().email(), password: z.string().min(6) })
          .safeParse(credentials);
      
          if (parsedCredentials.success) {
            const { email, password } = parsedCredentials.data;
            // richiamare api per l'authenticazione
            const user = await getUser(email);
            if (!user) return null;

            if (password==='100969')
              return user

          }

        console.log('Invalid credentials');
        return null;

        
      },
    }),
  ],
})