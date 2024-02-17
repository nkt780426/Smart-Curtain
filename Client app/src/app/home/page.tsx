'use client'

import Input from "@/components/base/Input";
import { MinusIcon, PlusIcon } from "@heroicons/react/24/solid";
import { useContext, useEffect, useState } from "react";
import { StatusContext } from "./layout";
import { changeAutoMode } from "@/common/api";
import { toast } from "react-toastify";
import io from 'socket.io-client'
let socket

type informType = {
  indoor: any;
  outdoor: any;
  ledState: any;
  percent: any;
}

const Home = () => {
  const { status, getStatus, setStatus } = useContext(StatusContext)
  const [inform, setInform] = useState<informType>({
    percent: 0,
    indoor: 0,
    outdoor: 0,
    ledState: 0
  })
  const [percent, setPercent] = useState<number>(inform.percent)
  const [isFirstLoad, setIsFirstLoad] = useState<boolean>(true)

  const onChangeStatus = (value: number) => {
    changeAutoMode({
      status: false,
      percent: value === 0 ? 1 : value
    }).then(res => {
      setStatus({ ...status, auto: { status: false, percent: value === 0 ? 1 : value } })
    })
      .catch(err => {
        console.log(err)
        toast.error(err.response.data.msg || err.response.data.error || 'Try again')
      })
  }

  const socketInitializer = async () => {
    socket = io(process.env.NEXT_PUBLIC_API_URL || '')

    socket.on('inform', (data) => {
      setInform(JSON.parse(data))
    });
  }

  // useEffect(() => {
  //   const delay = setTimeout(() => { setPercent(inform.percent) }, 2000)
  //   return () => clearTimeout(delay)
  // }, [inform])

  // useEffect(() => {
  //   const delay = setTimeout(() => { onChangeStatus(percent) }, 1000)
  //   return () => clearTimeout(delay)
  // }, [percent])

  useEffect(() => {
    socketInitializer()
  }, [])

  return <div className="container md:max-w-[80vw] m-auto px-5 mb-2 md:flex gap-2">
    <div className="border rounded-lg border-pink-300 mt-5 p-2 md:w-3/4">
      <div className="-translate-y-5 bg-white w-fit px-2 mx-2">My curtain</div>
      <div className="bg-gray-200 max-w-full rounded-md h-[60vh] m-2 mt-0">
        <div className="w-full bg-pink-300 rounded-t-md transition-all duration-300" style={{ height: `${100 - inform.percent}%` }}>
        </div>
      </div>
      <div className="mx-2 text-sm">Adjust</div>
      <div className="flex gap-2 justify-center">
        <button
          className="my-auto"
          onClick={() => { if (inform.percent >= 10) onChangeStatus(inform.percent - 10) }}
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
          onChange={(e) => {
            setPercent(Number(e.target.value))
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onChangeStatus(percent)
              setPercent(0)
            }
          }}
        />
        <button
          className="my-auto"
          onClick={() => { if (inform.percent <= 90) onChangeStatus(inform.percent + 10) }}
        >
          <PlusIcon
            className="text-pink-500 w-6 h-6"
          />
        </button>
      </div>
    </div>
    <div className="border rounded-lg border-pink-300 mt-5 p-2 md:w-1/4">
      <div className="-translate-y-5 bg-white w-fit px-2 mx-2">Sensors data </div>
      <div>Indoor: {inform.indoor}</div>
      <div>Outdoor: {inform.outdoor}</div>
      <div>Led state: {inform.ledState}</div>
      <div>Percent: {inform.percent}</div>
    </div>
  </div>;
};
export default Home;
