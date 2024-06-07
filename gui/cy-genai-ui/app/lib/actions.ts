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

export async function createContext(formData: FormData) {
  /*
  const { customerId, amount, status } = CreateInvoice.parse({
      customerId: formData.get('customerId'),
      amount: formData.get('amount'),
      status: formData.get('status'),
    });
   
  const amountInCents = amount * 100;  
  const date = new Date().toISOString().split('T')[0];
  
  try {
    await sql`
    INSERT INTO invoices (customer_id, amount, status, date)
    VALUES (${customerId}, ${amountInCents}, ${status}, ${date})`;
  } catch (error) {
  return {
    message: 'Database Error: Failed to Create Invoice.',
  };
}


  revalidatePath('/dashboard/invoices');
  redirect('/dashboard/invoices');

  // Test it out:
  //console.log(rawFormData);
  */
}
