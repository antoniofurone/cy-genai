'use server'
 
import { signIn } from '@/auth'
import { _createContext, _deleteContext,_updateContext } from './data'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
 
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
    console.log('id:'+id)
    _deleteContext(id)

    revalidatePath('/home');
    redirect('/home');

  } catch (error) {
    return { message: 'Database Error: Failed to Delete Context.' };
  }    
}

 

export async function createContext(formData: FormData) {

  _createContext(formData)
  
  revalidatePath('/home');
  redirect('/home');
  
}

export async function updateContext(id: number, formData: FormData) {

  _updateContext(id,formData)
  
  revalidatePath('/home');
  redirect('/home');
  


}
