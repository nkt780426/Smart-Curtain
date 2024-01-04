"use client";

import { Bars3Icon } from "@heroicons/react/24/solid";
import { useState, useRef, useEffect } from "react";
import { PinkButton } from "./base/Button";
import clsx from "clsx";
import { MinusIcon } from "@heroicons/react/24/outline";
import { ChartBarSquareIcon } from "@heroicons/react/20/solid";
import Switch from "./base/Switch";
import TimePicker from "react-time-picker";
import "react-clock/dist/Clock.css";

export const Header = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [automation, setAutomation] = useState<boolean>(false);
  const [manual, setManual] = useState<boolean>(false);

  return (
    <div className="px-4 py-2 bg-pink-300 relative">
      <div className=" m-auto flex justify-between ">
        <div className="flex gap-4">
          <PinkButton
            className="p-2 w-fit"
            onClick={() => setIsOpen((o) => !o)}
          >
            {isOpen ? (
              <MinusIcon className="w-6 h-6" />
            ) : (
              <Bars3Icon className="w-6 h-6" />
            )}
          </PinkButton>
          <span className="text-lg leading-10 w-full">IoT App</span>
        </div>
        <div>ava</div>
      </div>
      <ul
        className={clsx(
          "absolute max-w-[300px] top-full left-0 bg-pink-100 overflow-hidden transition-[width] duration-500 border-collapse",
          isOpen ? "w-[80%]" : "w-0"
        )}
        style={{ height: "calc(100vh - 56px)" }}
      >
        <li className="p-4 flex justify-between border-b border-pink-300 cursor-pointer">
          <div className="">Dashboard</div>
          <ChartBarSquareIcon className="w-6 h-6 text-pink-500" />
        </li>
        <li className="p-4 flex justify-between border-b border-pink-300">
          <div className="">Automation</div>
          <Switch
            checked={automation}
            onChange={() => setAutomation((o) => !o)}
            name="automation"
          />
        </li>
        <li className="p-4 flex justify-between border-b border-pink-300">
          <div className="">Manual</div>
          <Switch
            checked={manual}
            onChange={() => setManual((o) => !o)}
            name="manual"
          />
        </li>
        <li className="p-4 flex justify-between border-b border-pink-300 cursor-pointer">
          <div className="">Timer</div>
          <div className="bg-pink-500 w-6 h-6 text-sm text-center leading-6 rounded-full text-white">
            0
          </div>
        </li>
      </ul>
    </div>
  );
};
