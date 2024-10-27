'use client';

import { useState, useEffect } from 'react';
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { GridTileImage } from '@components/grid/tile';
import Image from 'next/image';

export function Gallery({ images }: { images: { src: string; altText: string }[] }) {
  const [imageIndex, setImageIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [imgSrc, setImgSrc] = useState(images[imageIndex].src);

  useEffect(() => {
    setLoading(true); // Set loading to true when the image index changes
    setImgSrc(images[imageIndex].src); // Reset the image source when the index changes
  }, [imageIndex]);

  const nextImageIndex = () => {
    setImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const previousImageIndex = () => {
    setImageIndex((prevIndex) => (prevIndex === 0 ? images.length - 1 : prevIndex - 1));
  };

  const selectImageIndex = (index: number) => {
    setImageIndex(index);
  };

  const handleImageError = () => {
    setImgSrc('/assets/images/emptyframe.png'); // Set fallback image source
  };

  const buttonClassName =
    'h-full px-6 transition-all ease-in-out hover:scale-110 hover:text-black dark:hover:text-white flex items-center justify-center';

  return (
    <>
      <div className="relative aspect-square h-full max-h-[550px] w-full overflow-hidden">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white ">
            <img src='/assets/images/img_loading.gif' alt="Loading..." />
          </div>
        )}
        {images[imageIndex] && (
          <Image
            className="h-full w-full object-contain"
            fill
            sizes="(min-width: 1024px) 66vw, 100vw"
            alt={images[imageIndex]?.altText as string}
            src={imgSrc}
            priority={true}
            onLoad={() => setLoading(false)}
            onError={handleImageError}
          />
        )}

        {images.length > 1 && (
          <div className="absolute bottom-[15%] flex w-full justify-center">
            <div className="mx-auto flex h-11 items-center rounded-full border border-white bg-neutral-50/80 text-neutral-500 backdrop-blur dark:border-black dark:bg-neutral-900/80">
              <button
                aria-label="Previous product image"
                onClick={previousImageIndex}
                className={buttonClassName}
              >
                <ArrowLeftIcon className="h-5" />
              </button>
              <div className="mx-1 h-6 w-px bg-neutral-500"></div>
              <button
                aria-label="Next product image"
                onClick={nextImageIndex}
                className={buttonClassName}
              >
                <ArrowRightIcon className="h-5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {images.length > 1 && (
        <ul className="my-12 flex items-center justify-center gap-2 overflow-x-auto py-1 lg:mb-0 no-scrollbar ">
          {images.map((image, index) => {
            const isActive = index === imageIndex;

            return (
              <li key={image.src} className="h-20 bg-white">
                <button
                  aria-label="Enlarge product image"
                  onClick={() => selectImageIndex(index)}
                  className="h-full w-full "
                >
                  <GridTileImage
                    alt={image.altText}
                    src={image.src}
                    width={80}
                    height={80}
                    active={isActive}
                  />
                </button>
              </li>
            );
          })}
        </ul>
      )}

      <style jsx>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none; /* Chrome, Safari, Opera */
        }
        .no-scrollbar {
          -ms-overflow-style: none;  /* IE and Edge */
          scrollbar-width: none;  /* Firefox */
        }
      `}</style>
    </>
  );
}
