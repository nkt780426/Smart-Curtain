"use client";

import { Bars3Icon } from "@heroicons/react/24/solid";
import { useState, useContext } from "react";
import { PinkButton } from "./base/Button";
import clsx from "clsx";
import { ArrowRightOnRectangleIcon, MinusIcon } from "@heroicons/react/24/outline";
import { ChartBarSquareIcon } from "@heroicons/react/20/solid";
import Switch from "./base/Switch";
import "react-clock/dist/Clock.css";
import { StatusContext } from "@/app/home/layout";
import Link from "next/link";
import { changeAutoMode } from "@/common/api";
import { toast } from "react-toastify";
import { useRouter } from "next/navigation";

export const Header = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const { status, getStatus } = useContext(StatusContext)
  const router = useRouter()

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
        {/* <div>ava</div> */}
      </div>
      <ul
        className={clsx(
          "absolute max-w-[300px] top-full left-0 bg-pink-100 overflow-hidden transition-[width] duration-300 border-collapse z-10",
          isOpen ? "w-[80%]" : "w-0"
        )}
        style={{ height: "calc(100vh - 56px)" }}
      >

        <li>
          <Link
            href='/home'
            className="p-4 flex justify-between border-b border-pink-300 cursor-pointer hover:bg-pink-200"
          >
            <div className="">Dashboard</div>
            <ChartBarSquareIcon className="w-6 h-6 text-pink-500" />
          </Link>
        </li>
        <li className="p-4 flex justify-between border-b border-pink-300">
          <div className="">Automation</div>
          <Switch
            checked={status.auto.status}
            onChange={() =>
              changeAutoMode({ status: !status.auto.status })
                .then(() => getStatus())
                .catch(err => {
                  console.log(err)
                  toast.error(err.response.data.msg || err.response.data.error || 'Try again')
                })
            }
            name="automation"
          />
        </li>
        <li>
          <Link
            href='/home/daily-alarm'
            className="p-4 flex justify-between border-b border-pink-300 cursor-pointer hover:bg-pink-200"
          >
            <div className="">Daily alarm</div>
            <div className="bg-pink-500 w-6 h-6 text-sm text-center leading-6 rounded-full text-white">
              {status.daily_alarm.length || 0}
            </div>
          </Link>
        </li>
        <li>
          <Link
            href='/home/once-alarm'
            className="p-4 flex justify-between border-b border-pink-300 cursor-pointer hover:bg-pink-200"
          >
            <div className="">Once alarm</div>
            <div className="bg-pink-500 w-6 h-6 text-sm text-center leading-6 rounded-full text-white">
              {status.once_alarm.length || 0}
            </div>
          </Link>
        </li>
        <li>
          <div
            onClick={() => {
              localStorage.removeItem('accessToken');
              router.push('/login')
            }}
            className="p-4 flex justify-between border-b border-pink-300 cursor-pointer hover:bg-pink-200"
          >
            <div className="">Log out</div>
            <ArrowRightOnRectangleIcon className="w-6 h-6 text-pink-500" />
          </div>
        </li>
      </ul>
    </div>
  );
};
