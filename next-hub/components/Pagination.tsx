"use client";
import { updateSearchParams } from "@utils";
import { useRouter } from "next/navigation";
import { CustomButton } from "@components";
import { useEffect, useState } from "react";

export interface PaginationProps {
    page: number;
    maxPages: number;
    isNext: boolean;
}

const Pagination = ({ page, maxPages, isNext }: PaginationProps) => {
    const router = useRouter();

    const currentPage = page;
    const hasNextPage = currentPage < maxPages;
    const hasPrevPage = currentPage > 1;

    const [scrollPosition, setScrollPosition] = useState(0); // State to store scroll position

    useEffect(() => {
        // Scroll to previous position when currentPage changes
        window.scrollTo(0, scrollPosition);
    }, [currentPage, scrollPosition]);

    const generatePageNumbers = () => {
        const pageNumbers = [];
        const pageCount = 5; 

        pageNumbers.push(1);
        if (currentPage > 2) {
            pageNumbers.push('...');
        }

        for (let i = currentPage - pageCount; i <= currentPage + pageCount; i++) {
            if (i > 1 && i < maxPages) {
                pageNumbers.push(i);
            }
        }

        if (currentPage < maxPages - 1) {
            pageNumbers.push('...');
            pageNumbers.push(maxPages);
        }

        return pageNumbers;
    };

    const goToPage = (pageNumber: number) => {
        localStorage.setItem('scrollPosition', String(window.scrollY));
        const pathname = updateSearchParams("page", `${pageNumber}`);
        router.push(pathname);
    };

    return (
        <div className="flex justify-center mt-10">
            <div className="flex items-center gap-2">
                {hasPrevPage && (
                    <CustomButton
                        btnType="button"
                        title="<<"
                        containerStyles="bg-blue-500 rounded-full text-white"
                        handleClick={() => goToPage(currentPage - 1)}
                    />
                )}
                {generatePageNumbers().map((pageNumber, index) => (
                    <span
                        key={index}
                        className={`cursor-pointer ${pageNumber === currentPage ? 'font-bold' : ''}`}
                        onClick={() => goToPage(Number(pageNumber))}
                    >
                        {pageNumber}
                    </span>
                ))}
                {hasNextPage && (
                    <CustomButton
                        btnType="button"
                        title=">>"
                        containerStyles="bg-blue-500 rounded-full text-white"
                        handleClick={() => goToPage(currentPage + 1)}
                    />
                )}
            </div>
        </div>
    );
};

export default Pagination;
