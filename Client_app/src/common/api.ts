/** @format */

import axios from 'axios';

export const API = axios.create({
	baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
});

API.interceptors.request.use((req) => {
	if (localStorage.getItem('profile')) {
		req.headers.authorization = `Bearer ${JSON.parse(
			localStorage.getItem('accessToken') || ''
		)}`;
	}
	return req;
});