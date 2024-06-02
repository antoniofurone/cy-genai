'use server'
 
import { signIn } from '@/auth'

 
export async function authenticate(_currentState: unknown, formData: FormData) {
  try {
    await signIn('credentials', formData)
   
  } catch (error) {
    if (error) {
      console.log(error)
      switch (error.type) {
        case 'CredentialsSignin':
          return 'Invalid credentials.'
        default:
          return 'Something went wrong.'
      }
      
    }
    throw error
  }
}

export async function deleteContext(id: number) {
  try {
    // await sql`DELETE FROM invoices WHERE id = ${id}`;
    // revalidatePath('/dashboard/invoices');
    return { message: 'Deleted Context.' };
  } catch (error) {
    return { message: 'Database Error: Failed to Delete Context.' };
  }    
}