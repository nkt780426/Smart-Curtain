'use client'

import Input from "@/components/base/Input";
import { MinusIcon, PlusIcon } from "@heroicons/react/24/solid";
import { useContext, useEffect, useState } from "react";
import { StatusContext } from "./layout";
import { changeAutoMode } from "@/common/api";
import { toast } from "react-toastify";

const Home = () => {
  const { status, getStatus } = useContext(StatusContext)
  const [percent, setPercent] = useState<number>(status.auto.percent)

  const onChangeStatus = (value: number) => {
    console.log(value)
    console.log(localStorage.getItem('accessToken'))

    changeAutoMode({
      status: false,
      percent: value
    }).then(res => {
      getStatus()
    })
      .catch(err => {
        console.log(err)
        toast.error(err.response.data.msg || err.response.data.error || 'Try again')
      })
  }

  useEffect(() => {
    console.log(localStorage.getItem('accessToken'))
    setPercent(status.auto.percent)
  }, [status])

  // useEffect(() => {
  //   const timeout = setTimeout(() => onChangeStatus(percent), 1000)
  //   return () => clearTimeout(timeout)
  // }, [percent])

  return <div className="container md:max-w-[80vw] m-auto px-5 mb-2 md:flex gap-2">
    <div className="border rounded-lg border-pink-300 mt-5 p-2 md:w-3/4">
      <div className="-translate-y-5 bg-white w-fit px-2 mx-2">My curtain</div>
      <div className="bg-gray-200 max-w-full rounded-md h-[60vh] m-2 mt-0">
        <div className="w-full bg-pink-300 rounded-t-md" style={{ height: `${status.auto.percent}%` }}>
        </div>
      </div>
      <div className="mx-2 text-sm">Adjust</div>
      <div className="flex gap-2 justify-center">
        <button
          className="my-auto"
          onClick={() => { if (status.auto.percent >= 10) onChangeStatus(status.auto.percent - 10) }}
        >
          <MinusIcon
            className="text-pink-500 w-6 h-6"
          />
        </button>
        <Input
          className="flex-none w-[100px] text-center"
          type="number"
          min={0}
          max={100}
          value={percent}
          onChange={(e) => setPercent(Number(e.target.value))}
        />
        <button
          className="my-auto"
          onClick={() => { if (status.auto.percent <= 90) onChangeStatus(status.auto.percent + 10) }}
        >
          <PlusIcon
            className="text-pink-500 w-6 h-6"
          />
        </button>
      </div>
    </div>
    <div className="border rounded-lg border-pink-300 mt-5 p-2 md:w-1/4">
      <div className="-translate-y-5 bg-white w-fit px-2 mx-2">Sensors data </div>
      <div>Indoor: 1</div>
      <div>Outdoor: 1</div>
      <div>Led state: 1</div>
    </div>
  </div>;
};
export default Home;
