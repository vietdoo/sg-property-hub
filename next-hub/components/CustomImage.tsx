"use client";

import { useState } from "react";
import Image from "next/image";

export interface CustomImageProps {
    src: string;
    alt: string;
    fill?: boolean;
    priority?: boolean;
    className?: string;
    objectFit?: "cover" | "contain" | "fill";
}

const CustomImage: React.FC<CustomImageProps> = ({ src, alt, fill, priority, className, objectFit = "cover" }) => {
    const [imgSrc, setImgSrc] = useState(src);

    const handleError = () => {
        setImgSrc('/assets/images/emptyframe.png');
    };

    return (
        <Image
            src={imgSrc}
            alt={alt}
            fill={fill}
            priority={priority}
            className={className}
            style={{ objectFit }}
            onError={handleError}
        />
    );
};

export default CustomImage;