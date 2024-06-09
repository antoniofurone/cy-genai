import Form from '@/app/ui/home/edit-form';
import Breadcrumbs from '@/app/ui/home/breadcrumbs';
import { fetchContextById, fetchEmbeddingTypes,fetchContextTypes } from '@/app/lib/data';
import { notFound } from 'next/navigation';
 
export default async function Page({ params }: { params: { id: number } }) {
const id = params.id; 
const [context, embTypes, contextTypes] = await Promise.all([
    fetchContextById(id),
    fetchEmbeddingTypes(),
    fetchContextTypes()
  ]); 

  if (!context) {
    notFound();
  }
  
  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: 'Contexts', href: '/homr' },
          {
            label: 'Edit Context',
            href: `/home/${id}/edit`,
            active: true,
          },
        ]}
      />
      <Form context={context} embTypes={embTypes} contextTypes={contextTypes} />
    </main>
  );
}

export const metadata = {
  title: "CyGenAI UI",
  description: "CyGenAI User Interface",
}