import React, { FormEventHandler } from "react";
import { Switch as HLSWitch } from "@headlessui/react";
import clsx from "clsx";

type Props = {
  checked: boolean;
  onChange:
    | ((checked: boolean) => void)
    | (FormEventHandler<HTMLButtonElement> & ((checked: boolean) => void));
  name: string;
};

function Switch({ checked, name, onChange }: Props) {
  return (
    <HLSWitch
      checked={checked}
      onChange={onChange}
      className={clsx(
        checked ? "bg-pink-500" : "bg-gray-300",
        "relative inline-flex flex-shrink-0 h-6 w-[40px] border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus-visible:ring-2  focus-visible:ring-white focus-visible:ring-opacity-75"
      )}
    >
      <span className="sr-only">{name}</span>
      <span
        aria-hidden="true"
        className={clsx(
          checked ? "translate-x-4" : "translate-x-1",
          "pointer-events-none inline-block h-4 w-4 rounded-full bg-white shadow-lg transform ring-0 transition ease-in-out duration-200 my-auto"
        )}
      />
    </HLSWitch>
  );
}

export default Switch;
