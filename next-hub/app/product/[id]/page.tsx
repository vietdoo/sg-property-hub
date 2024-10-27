import { fetchHouse, fetchHouses } from "@utils";
import Link from 'next/link';
import { Suspense } from 'react';

import { ProductDescription } from '@components/product/product-description';
import { ProductInsight } from '@components/product/product-insight';
import { ProductDetails } from '@components/product/product-details';
import { PinMap } from '@components/product/pin-map';
import { Gallery } from '@components/product/gallery';
import { GridTileImage } from '@components/grid/tile';


export interface PageProps {
  params: {
    id: string
  }
}
 
export default async function Page({params}: PageProps ) {
  const {id} = params;
  const data = await fetchHouse(id);
  
  const house = data;

  if (!house) {

    return (
      <div className="flex items-center justify-center min-h-screen">
        <h1 className="text-center text-2xl font-bold">Not Found</h1>
      </div>
    )
  }

  return (
    <>
      <script
        type="application/ld+json"
      />
      <div className="mx-auto max-w-screen-2xl px-4">
        <div className="flex flex-col rounded-lg border border-neutral-200 bg-white p-8  dark:bg-white md:p-12 lg:flex-row lg:gap-8">
          <div className="h-full w-full basis-full lg:basis-4/6">
            <Suspense>
            <Gallery
              images={house.image.map((image:any) => ({
                src: image,
                altText: 'house model'
              }))}
            />
            </Suspense>
          </div>

          <div className="basis-full lg:basis-2/6">
            <ProductDescription product={house} />
          </div>
        </div>
        <div className="flex flex-col rounded-lg border border-neutral-200 bg-white p-8  dark:bg-white mt-10 md:p-12 lg:flex-row lg:gap-8">
          <ProductInsight product={house} />
          <ProductDetails product={house} />

        </div>

        <div className="flex flex-col rounded-lg border border-neutral-200 bg-white p-8  dark:bg-white mt-10 md:p-12 lg:flex-row lg:gap-8">
          <PinMap 
            lat={house.location_lat} 
            long={house.location_long}  
            thumbnail={house.image[0]}
          />

        </div>
        <Suspense>
          <RelatedProducts id={id} />
        </Suspense>
      </div>
    </>
  );
}

async function RelatedProducts({ id }: { id: string }) {
  const house = await fetchHouse(id);
  if (!house) return null;
  const house_city = house.location_city;
  const random_offset = Math.floor(Math.random() * 100);

  const relatedProducts = await fetchHouses({limit: 8, offset: random_offset, city: house_city});

  if (!relatedProducts.length) return null;

  return (
    <div className="py-8">
      <h2 className="mb-4 text-2xl font-bold">Related Products</h2>
      <ul className="flex w-full gap-4 overflow-x-auto pt-1">
        {relatedProducts.map((product:any) => (
          <li
            key={product.title}
            className="aspect-square w-full flex-none min-[475px]:w-1/2 sm:w-1/3 md:w-1/4 lg:w-1/5"
          >
            <Link className="relative h-full w-full" href={`/product/${product.id}`}>
              <GridTileImage
                alt={product.title}
                label={{
                  title: product.title,
                  amount: product.price.toString(),
                  currencyCode: 'VND'
                }}
                src={product.image[0]}
                fill
                sizes="(min-width: 1024px) 20vw, (min-width: 768px) 25vw, (min-width: 640px) 33vw, (min-width: 475px) 50vw, 100vw"
                style={{ objectFit: "cover" }}
              />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}