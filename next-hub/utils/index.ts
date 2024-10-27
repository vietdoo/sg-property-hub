// "use client";

import { HouseProps, FilterProps } from "@types";
import useSWR from 'swr'


export const updateSearchParams = (type: string, value: string) => {
  const searchParams = new URLSearchParams(window.location.search);
  searchParams.set(type, value);
  const newPathname = `${window.location.pathname}?${searchParams.toString()}`;

  return newPathname;
};

export const deleteSearchParams = (type: string) => {

  const newSearchParams = new URLSearchParams(window.location.search);
  newSearchParams.delete(type.toLocaleLowerCase());
  const newPathname = `${window.location.pathname}?${newSearchParams.toString()}`;

  return newPathname;
};

export async function fetchHouses(
    filters: FilterProps
  ) {
  const { category, dist, city, q, page, limit, lat_tl, long_tl, lat_br, long_br} = filters;
  
  const offset = (page || 0) * (limit || 24);
  var url = `${process.env.API_URL}/api/products?limit=${limit || 24}&offset=${offset}&q=${q || ''}`;
  
  
  if (category) {
    url = url.concat(`&category=${category}`);
  }
  
  if (dist) {
    url = url.concat(`&dist=${dist}`);
  }

  if (city) {
    url = url.concat(`&city=${city}`);
  }

  if (lat_tl && long_tl && lat_br && long_br) {
    url = url.concat(`&lat_tl=${lat_tl}&long_tl=${long_tl}&lat_br=${lat_br}&long_br=${long_br}`);
  }
  // console.log('Filters: ', filters);
  // console.log('Fetching houses from API: ', url);
  const response = await fetch(url);
  const result = await response.json();
  
  return result;
}

export async function fetchHouse(id: string) {
  try {
    const url =`${process.env.API_URL}/api/product?id=${id}`
    const response = await fetch(url);
 
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const result = await response.json();
    if (result.error) {
      throw new Error(result.error);
    }
    return result;
    } catch (error) {
      return null;
    }
}






const fetcher = (url:string) => fetch(url, {mode: 'no-cors'}).then(res => res)

// export function fetchHouse(
//     id: string
//   ) {

//   const { data, error, isLoading } = useSWR(`https://api.vietdoo.engineer/api/products?limit=1`, fetcher)
//   return {
//     data: data,
//     isLoading,
//     isError: error
//   }
// }

export const generatePrice = (price:number) => {
  //add dots to price
  const price_string = price.toLocaleString()
  return `${price_string}`;
} 

