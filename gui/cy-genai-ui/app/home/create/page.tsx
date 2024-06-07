import Form from '@/app/ui/home/create-form';
import Breadcrumbs from '@/app/ui/home/breadcrumbs';
import { fetchEmbeddingTypes } from '@/app/lib/data';
import { fetchContextTypes } from '@/app/lib/data';
 
export default async function Page() {
  const embTypes = await fetchEmbeddingTypes();
  const contextTypes = await fetchContextTypes();
 
  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: 'Contexts', href: '/home' },
          {
            label: 'Create Context',
            href: '/home/create',
            active: true,
          },
        ]}
      />
      <Form embTypes={embTypes} />
    </main>
  );
}