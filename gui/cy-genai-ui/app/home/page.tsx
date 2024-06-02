import Pagination from '@/app/ui/home/pagination';
import Search from '@/app/ui/search';
import Table from '@/app/ui/home/table';
import { CreateContext } from '@/app/ui/home/buttons';
import { lusitana } from '@/app/ui/fonts';
import { ContextsTableSkeleton } from '@/app/ui/skeletons';
import { Suspense } from 'react';
import { fetchContextPages } from '@/app/lib/data';
 
export default async function Page({
  searchParams,
}: {
  searchParams?: {
    query?: string;
    page?: string;
  };
}) {
  const query = searchParams?.query || '';
  const currentPage = Number(searchParams?.page) || 1;

  const totalPages = await fetchContextPages(query);
 

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>Contexts</h1>
      </div>
      <div className="mt-4 flex items-center justify-between gap-2 md:mt-8">
        <Search placeholder="Search contexts..." />
        {<CreateContext />}
      </div>
      
      <Suspense key={query + currentPage} fallback={<ContextsTableSkeleton />}>
        {<Table query={query} currentPage={currentPage} />}
      </Suspense> 
      
      <div className="mt-5 flex w-full justify-center">
        { <Pagination totalPages={totalPages} /> }
      </div>
    </div>
  );
}

export const metadata = {
  title: "CyGenAI UI",
  description: "CyGenAI User Interface",
}