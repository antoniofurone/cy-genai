'use client';

import { updateContext } from '@/app/lib/actions';
import {
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { Button } from '@/app/ui/button';

export default function EditInvoiceForm
  ({ embTypes,contextTypes,context }: { 
    embTypes: {id: number;name: string;}[],
    contextTypes: {id: number;name: string;}[],
    context:{id:number,
      context_name:string,
      chunk_size:number,
      chunk_overlap:number,
      context_size:number,
      chunk_threshold:number,
      load_threshold:number,
      chunk_weight:number,
      load_weight:number,
      embedding_model:number,
      context_type:number,
      history:boolean
    }
  })
 {
  const updateContextWithId = updateContext.bind(null, context.id);

  return (
    <form action={updateContextWithId}>
      <div className="rounded-md bg-gray-50 p-4 md:p-6">
        
        {/* Context Name */}
        <div className="mb-4">
          <label htmlFor="name" className="mb-2 block text-sm font-medium">
            Choose a name
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="name"
                name="name"
                type="string"
                placeholder="Enter name of context"
                defaultValue={context.context_name}
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
             
            </div>
          </div>
        </div>

        {/* Chunch Size */}
        <div className="mb-4">
          <label htmlFor="chunk_size" className="mb-2 block text-sm font-medium">
            Choose a chunk size
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="chunk_size"
                name="chunk_size"
                type="number"
                step="1"
                placeholder="Enter chunk size of context"
                defaultValue={context.chunk_size}
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

       {/* Chunch Overlap */}
       <div className="mb-4">
          <label htmlFor="chunk_overlap" className="mb-2 block text-sm font-medium">
            Choose a chunk overlap 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="chunk_overlap"
                name="chunk_overlap"
                type="number"
                defaultValue={context.chunk_overlap}
                step="1"
                placeholder="Enter chunk overlap of context"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

        {/* Context size */}
        <div className="mb-4">
          <label htmlFor="context_size" className="mb-2 block text-sm font-medium">
            Choose a context size 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="context_size"
                name="context_size"
                type="number"
                defaultValue={context.context_size}
                step="1"
                placeholder="Enter number of chunk used to build context"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

         {/* Chunk Threshold */}
         <div className="mb-4">
          <label htmlFor="chunk_threshold" className="mb-2 block text-sm font-medium">
            Choose a chunk threshold 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="chunk_threshold"
                name="chunk_threshold"
                type="number"
                defaultValue={context.chunk_threshold}
                step="0.01"
                placeholder="Enter chunk threshold for similarity"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

        {/* Load Threshold */}
        <div className="mb-4">
          <label htmlFor="load_threshold" className="mb-2 block text-sm font-medium">
            Choose a load threshold 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="load_threshold"
                name="load_threshold"
                type="number"
                defaultValue={context.load_threshold}
                step="0.01"
                placeholder="Enter load threshold for similarity"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

        {/* Chunk Weight */}
        <div className="mb-4">
          <label htmlFor="load_threshold" className="mb-2 block text-sm font-medium">
            Choose a chunk weight 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="chunk_weight"
                name="chunk_weight"
                type="number"
                defaultValue={context.chunk_weight}
                step="0.01"
                placeholder="Enter chunk weight for similarity"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

        {/* Load Weight */}
        <div className="mb-4">
          <label htmlFor="load_weight" className="mb-2 block text-sm font-medium">
            Choose a load weight 
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="load_weight"
                name="load_weight"
                type="number"
                defaultValue={context.load_weight}
                step="0.01"
                placeholder="Enter load weight for similarity"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
                required
              />
              
            </div>
          </div>
        </div>

         {/* Embedding Model */}
         <div className="mb-4">
          <label htmlFor="embedding_model" className="mb-2 block text-sm font-medium">
            Embedding Model
          </label>
          <div className="relative">
            <select
              id="embedding_model"
              name="embedding_model"
              className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
              defaultValue={context.embedding_model}
              required
            >
              <option value="" disabled>
                Select a embedding model
              </option>
              {embTypes.map((embType) => (
                <option key={embType.id} value={embType.id}>
                  {embType.name}
                </option>
              ))}
            </select>
            
          </div>
        </div>

        {/* Context Type */}
        <div className="mb-4">
          <label htmlFor="context_type" className="mb-2 block text-sm font-medium">
            Context Type
          </label>
          <div className="relative">
            <select
              id="context_type"
              name="context_type"
              className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
              defaultValue={context.context_type}
              required
            >
              <option value="" disabled>
                Select a context type
              </option>
              {contextTypes.map((contextType) => (
                <option key={contextType.id} value={contextType.id}>
                  {contextType.name}
                </option>
              ))}
            </select>
            
          </div>
        </div>

        {/* History */}
        <fieldset>
          <legend className="mb-2 block text-sm font-medium">
            Select if context has history
          </legend>
          <div className="rounded-md border border-gray-200 bg-white px-[14px] py-3">
            <div className="flex gap-4">
              <div className="flex items-center">
                <input
                  id="no-history"
                  name="history"
                  type="radio"
                  value="false" 
                  defaultChecked={context.history==false?true:false}
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="false"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600"
                >
                  False <XMarkIcon className="h-4 w-4" />
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="history"
                  name="history"
                  type="radio"
                  value="true"
                  defaultChecked={context.history==true?true:false}
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="true"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-green-500 px-3 py-1.5 text-xs font-medium text-white"
                >
                  True <CheckIcon className="h-4 w-4" />
                </label>
              </div>
            </div>
          </div>
        </fieldset>



      </div>
             
      <div className="mt-6 flex justify-end gap-4">
        <Link
          href="/home"
          className="flex h-10 items-center rounded-lg bg-gray-100 px-4 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-200"
        >
          Cancel
        </Link>
        <Button type="submit">Edit Context</Button>
      </div>
    </form>
  );
}
