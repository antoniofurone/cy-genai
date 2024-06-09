import { PrismaClient} from '@prisma/client'
import {Context} from './definitions'
const prisma = new PrismaClient()


const ITEMS_PER_PAGE = 6;

export async function fetchContextPages(query: string) {
  try {
    const count=await prisma.cy_context.count({
      where: {
      context_name:{
          startsWith:query
      }
    }
    });

    const totalPages = Math.ceil(Number(count) / ITEMS_PER_PAGE);
    return totalPages;
  } catch (error) {
    console.error('Database Error:', error);
    throw new Error('Failed to fetch total number of invoices.');
  }
}

export async function fetchFilteredContexts(
  query: string,
  currentPage: number,) 
{
  const offset = (currentPage - 1) * ITEMS_PER_PAGE;

  try {
    
      const contexts=prisma.cy_context.findMany({
        where: {
          OR: [
            {context_name:{startsWith:query}},
            {cy_embs_types:{name:{startsWith:query}}},
            {cy_context_types:{name:{startsWith:query}}}
        ]
        },
        include:{cy_embs_types:true,cy_context_types:true},
        orderBy: {id: 'asc'},
        skip:offset, take:ITEMS_PER_PAGE
 
        }
      );

    return contexts;
  } catch (error) {
    console.error('Database Error:', error);
    throw new Error('Failed to fetch contexts.');
  }
}

export async function fetchEmbeddingTypes() 
{
  try { 
    const embTypes=prisma.cy_embs_types.findMany();
    return embTypes;
  } catch (error) {
    console.error('Database Error:', error);
    throw new Error('Failed to fetch embedding types.');
  }

}


export async function fetchContextTypes() 
{
  try { 
    const embTypes=prisma.cy_context_types.findMany();
    return embTypes;
  } catch (error) {
    console.error('Database Error:', error);
    throw new Error('Failed to fetch context types.');
  }

}

export async function fetchContextById(id:number){

  const context=await prisma.cy_context.findUnique({
    where: { id: Number(id) },
  })

  return context;

}


export async function _deleteContext(id:number){

  const context=await prisma.cy_context.delete({
    where: { id: id },
  })

}


export async function _updateContext(id:number,form:FormData){

  const createContext = await prisma.cy_context.update({ 
    where: { id: id as number },
    data: {
    context_name: form.get('name') as string,
    chunk_size: Number(form.get('chunk_size')),
    chunk_overlap:Number(form.get('chunk_overlap')),
    context_size:Number(form.get('context_size')),
    chunk_threshold:Number(form.get('chunk_threshold')),
    load_threshold:Number(form.get('load_threshold')),
    chunk_weight:Number(form.get('chunk_weight')),
    load_weight:Number(form.get('load_weight')),
    cy_embs_types:{
      connect:{
        id:Number(form.get('embedding_model'))
      }},
    cy_context_types: {
      connect:{
        id:Number(form.get('context_type'))
      }
    },
    history:form.get('history') as string=='true'?true:false

  } })

}

export async function _createContext(form:FormData){

  //let context: Prisma.cy_contextCreateInput 
  /*
  context = {
    context_name: form.get('name') as string,
    chunk_size: Number(form.get('chunk_size')),
    chunk_overlap:Number(form.get('chunk_overlap')),
    context_size:Number(form.get('context_size')),
    chunk_threshold:Number(form.get('chunk_threshold')),
    load_threshold:Number(form.get('load_threshold')),
    chunk_weight:Number(form.get('chunk_weight')),
    load_weight:Number(form.get('load_weight')),
    cy_embs_types:{
      connect:{
        id:Number(form.get('embedding_model'))
      }},
    cy_context_types: {
      connect:{
        id:Number(form.get('context_type'))
      }
    },
    history:form.get('history') as string=='true'?true:false
  }
  */
  const createContext = await prisma.cy_context.create({ data: {
    context_name: form.get('name') as string,
    chunk_size: Number(form.get('chunk_size')),
    chunk_overlap:Number(form.get('chunk_overlap')),
    context_size:Number(form.get('context_size')),
    chunk_threshold:Number(form.get('chunk_threshold')),
    load_threshold:Number(form.get('load_threshold')),
    chunk_weight:Number(form.get('chunk_weight')),
    load_weight:Number(form.get('load_weight')),
    cy_embs_types:{
      connect:{
        id:Number(form.get('embedding_model'))
      }},
    cy_context_types: {
      connect:{
        id:Number(form.get('context_type'))
      }
    },
    history:form.get('history') as string=='true'?true:false

  } })
  
} 

