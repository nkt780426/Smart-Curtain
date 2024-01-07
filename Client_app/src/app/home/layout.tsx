'use client'

import { getStatusApi } from "@/common/api";
import { Header } from "@/components/Header";
import { createContext, useEffect, useState } from "react";
import { toast } from "react-toastify";

type StatusType = {
  auto: {
    status: boolean;
    percent: number;
  };
  daily_alarm: Array<{
    percent: number;
    hours: number;
    minutes: number;
  }>
  once_alarm: Array<{
    percent: number;
    specify_time: string;
  }>
}

const defaultStatus: StatusType = {
  auto: {
    status: false,
    percent: 0
  },
  daily_alarm: [],
  once_alarm: []
}

export const StatusContext = createContext<any>({})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [status, setStatus] = useState<StatusType>(defaultStatus)
  const getStatus = () => {
    getStatusApi()
      .then(res => {
        if (res.data) {
          // localStorage.setItem('accessToken', res.data.access_token)
        }
      })
      .catch(err => {
        console.log(err)
        toast.error(err.response.data.msg || err.response.data.error || 'Try again')
      })
  }

  useEffect(() => getStatus, [])
  return (
    <main>
      <StatusContext.Provider value={{ status, setStatus, getStatus }}>
        <Header />
        {children}
      </StatusContext.Provider>
    </main>
  );
}
