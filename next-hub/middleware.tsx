// import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// const isPublicRoute = createRouteMatcher(['/signin', '/signup', '/']);

// // export default clerkMiddleware((auth, request) => {
// //     if (!isPublicRoute(request)) {
// //         auth().protect();
// //     }
// // });
// export default clerkMiddleware();
// export const config = {
//     matcher: ["/((?!.*\\..*|_next).*)", "/", "/(api|trpc)(.*)"],
// }

export default function middleware() {
}