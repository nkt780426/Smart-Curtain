'use client'

import Input from "@/components/base/Input";
import { MinusIcon, PlusIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { useContext, useEffect, useState } from "react";
import { StatusContext } from "../layout";
import { postDailyAlarm } from "@/common/api";
import { toast } from "react-toastify";
import TimePicker from "react-time-picker";
import 'react-time-picker/dist/TimePicker.css';
import 'react-clock/dist/Clock.css';
import { ErrorText } from "@/components/base/ErrorText";
import { PinkButton } from "@/components/base/Button";
import * as yup from 'yup'
import { Controller, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import DatePicker from "react-datepicker";
import { registerLocale, setDefaultLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import vi from 'date-fns/locale/vi';
registerLocale('vi', vi)

const OnceAlarmSchema = yup.object().shape({
  percent: yup
    .number()
    .required('Percent is required')
    .min(0, 'Min of percent is 0')
    .max(100, 'Max of percent is 0'),
  specify_time: yup
    .date()
    .required('Time is required')
});

const DailyAlarm = () => {
  const { status, getStatus } = useContext(StatusContext)
  const [isAdd, setIsAdd] = useState<boolean>(false)
  const [percent, setPercent] = useState<number>(status.auto.percent)

  const {
    register,
    control,
    formState: { errors },
    handleSubmit,
  } = useForm({ resolver: yupResolver(OnceAlarmSchema), defaultValues: { specify_time: new Date() } })

  const onSubmit = (data: any) => {
    postDailyAlarm({
      percent: data.percent,
      hours: Number(data.time.split(':')[0]),
      minutes: Number(data.time.split(':')[1]),
    }).then(res => {
      setTimeout(() => getStatus(), 100)
    })
      .catch(err => {
        console.log(err)
        toast.error(err.response.data.msg || err.response.data.error || 'Try again')
      })
  }
  return <div className="container md:max-w-[80vw] m-auto px-5 mt-4">
    <div className="flex justify-between">
      <span className="text-xl">Once Alarm</span>
      <button
        onClick={() => setIsAdd(true)}
      >
        <PlusIcon
          className="text-pink-500 w-6 h-6"
        />
      </button>

    </div>
    {isAdd &&
      <div className="border rounded-lg border-pink-300 mt-5 px-4 pb-4">
        <div className="-translate-y-3 bg-white w-fit px-2 mx-2">Add once alarm </div>
        <div className="text-sm">Time</div>
        <Controller
          name="specify_time"
          control={control}
          render={({ field }) => <DatePicker />}
        />
        <ErrorText>{errors.specify_time?.message}</ErrorText>
        <div className="text-sm">Percent</div>
        <Input
          className='flex-1 w-full'
          type="number"
          max={100}
          min={0}
          {...register('percent')}
        />
        <ErrorText>{errors.percent?.message}</ErrorText>

        <div className='flex gap-2 mt-3'>
          <PinkButton className='w-fit' onClick={handleSubmit(onSubmit)}>Add</PinkButton>

          <button>
            <XMarkIcon
              className="text-pink-500 w-6 h-6 my-auto"
            />
          </button>
        </div>
      </div>}
    <ul>
      {status.daily_alarm.map((e: any, id: number) => <li key={id}>
        <span>{e.hours}:{e.minutes}</span>
        <span>{e.percent}%</span>
        <button>
          <MinusIcon className="text-pink-500 w-6 h-6" />
        </button>
      </li>)}
    </ul>
  </div>;
};
export default DailyAlarm;
