import clsx from 'clsx';

import React from 'react';

export default function LogoIcon(props: React.ComponentProps<'img'>) {
  return (
    <img
      src="/logo.png" // Thay thế đường dẫn bằng đường dẫn đến tệp PNG của bạn
      alt="SGP Hub logo"
      {...props}
      className={clsx('h-4 w-4', props.className)}
    />
  );
}
