'use client'

import Input from "@/components/base/Input";
import { MinusIcon, PlusIcon, XMarkIcon } from "@heroicons/react/24/solid";
import { useContext, useEffect, useState } from "react";
import { StatusContext } from "../layout";
import { postDailyAlarm, postOnceAlarm } from "@/common/api";
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
    const newdate = new Date(data.specify_time)
    const tmp = `${newdate.getFullYear()}-${newdate.getMonth() + 1}-${newdate.getDate()}-${newdate.getHours()}-${newdate.getMinutes()}`

    postOnceAlarm({
      percent: data.percent,
      specify_time: tmp
    }).then(res => {
      getStatus()
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
          render={({ field }) => <DatePicker
            onChange={(e) => field.onChange(e)}
            selected={field.value}
            // locale={'vi'}
            showTimeInput
            dateFormat='dd/MM/yyyy h:mm aa'
          />}
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
      {status.once_alarm.map((e: any, id: number) => <li key={id} className='flex justify-between w-full text-lg'>
        <div className="font-semibold">{
          new Date(e.specify_time).toDateString() +
          new Date(e.specify_time).toTimeString()}</div>
        <div className="flex gap-10 my-1">
          <div>{e.percent}%</div>
        <button>
          <MinusIcon className="text-pink-500 w-6 h-6" />
        </button>
        </div>
      </li>)}
    </ul>
  </div>;
};
export default DailyAlarm;
