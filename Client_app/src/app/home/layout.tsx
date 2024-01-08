'use client'

import { getStatusApi } from "@/common/api";
import { Header } from "@/components/Header";
import { useRouter } from "next/navigation";
import { createContext, useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import io from 'socket.io-client'
let socket

type StatusType = {
  auto: {
    status: boolean;
    percent: number;
  };
  daily_alarm: Array<{
    percent: number;
    hours: number;
    minutes: number;
    username: string;
    job_id: string;
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

export const StatusContext = createContext<any>(undefined)

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
          setStatus(res.data)
        }
      })
      .catch(err => {
        console.log(err)
        toast.error(err.response.data.msg || err.response.data.error || 'Try again')
      })
  }
  const router = useRouter()

  const socketInitializer = useCallback(() => {
    async () => {
    socket = io(process.env.NEXT_PUBLIC_API_URL || '')

    socket.on('esp32_status', (data) => {
      const res = JSON.parse(data).activate
      if (res === false) {
        router.push('/home/disconnect')
      }
    })
    socket.on('auto_mode', (data) => {
      getStatus()
    });

    }
  }, [router]);

  useEffect(() => {
    getStatus()
    socketInitializer()
  }, [socketInitializer])
  return (
    <main>
      <StatusContext.Provider value={{ status, setStatus, getStatus }}>
        <Header />
        {children}
      </StatusContext.Provider>
    </main>
  );
}
