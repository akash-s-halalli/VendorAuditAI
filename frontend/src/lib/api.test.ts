import { describe, it, expect, beforeEach } from 'vitest';
import axios, { AxiosError, AxiosHeaders } from 'axios';
import { apiClient, getApiErrorMessage, ApiError } from './api';

describe('apiClient', () => {
  it('has correct base URL configuration', () => {
    expect(apiClient.defaults.baseURL).toContain('/api/v1');
  });

  it('has correct default headers', () => {
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('has timeout configured', () => {
    expect(apiClient.defaults.timeout).toBe(30000);
  });

  describe('request interceptor', () => {
    beforeEach(() => {
      localStorage.clear();
    });

    it('adds Authorization header when token exists', async () => {
      localStorage.setItem('access_token', 'test-token-123');

      // Create a mock config object
      const config = {
        headers: new AxiosHeaders(),
        url: '/test',
        method: 'get' as const,
      };

      // Get the request interceptor and run it
      const interceptors = (apiClient.interceptors.request as unknown as { handlers: Array<{ fulfilled: (config: unknown) => unknown }> }).handlers;
      const requestInterceptor = interceptors[0]?.fulfilled;

      if (requestInterceptor) {
        const result = requestInterceptor(config) as { headers: AxiosHeaders };
        expect(result.headers.get('Authorization')).toBe('Bearer test-token-123');
      }
    });

    it('does not add Authorization header when no token', async () => {
      const config = {
        headers: new AxiosHeaders(),
        url: '/test',
        method: 'get' as const,
      };

      const interceptors = (apiClient.interceptors.request as unknown as { handlers: Array<{ fulfilled: (config: unknown) => unknown }> }).handlers;
      const requestInterceptor = interceptors[0]?.fulfilled;

      if (requestInterceptor) {
        const result = requestInterceptor(config) as { headers: AxiosHeaders };
        expect(result.headers.get('Authorization')).toBeFalsy();
      }
    });
  });
});

describe('getApiErrorMessage', () => {
  it('returns message from API error response', () => {
    const error = new AxiosError('Request failed');
    error.response = {
      status: 400,
      statusText: 'Bad Request',
      data: {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid input data',
        } as ApiError,
      },
      headers: {},
      config: { headers: new AxiosHeaders() },
    };

    expect(getApiErrorMessage(error)).toBe('Invalid input data');
  });

  it('returns "Resource not found" for 404 errors without message', () => {
    const error = new AxiosError('Request failed');
    error.response = {
      status: 404,
      statusText: 'Not Found',
      data: {},
      headers: {},
      config: { headers: new AxiosHeaders() },
    };

    expect(getApiErrorMessage(error)).toBe('Resource not found');
  });

  it('returns "Server error" for 500 errors without message', () => {
    const error = new AxiosError('Request failed');
    error.response = {
      status: 500,
      statusText: 'Internal Server Error',
      data: {},
      headers: {},
      config: { headers: new AxiosHeaders() },
    };

    expect(getApiErrorMessage(error)).toBe('Server error. Please try again later.');
  });

  it('returns axios error message when no API error data', () => {
    const error = new AxiosError('Network Error');
    expect(getApiErrorMessage(error)).toBe('Network Error');
  });

  it('returns error message from standard Error', () => {
    const error = new Error('Something went wrong');
    expect(getApiErrorMessage(error)).toBe('Something went wrong');
  });

  it('returns generic message for unknown error types', () => {
    expect(getApiErrorMessage('string error')).toBe('An unexpected error occurred');
    expect(getApiErrorMessage(null)).toBe('An unexpected error occurred');
    expect(getApiErrorMessage(undefined)).toBe('An unexpected error occurred');
    expect(getApiErrorMessage(123)).toBe('An unexpected error occurred');
  });

  it('handles axios error with response but no error field', () => {
    const error = new AxiosError('Request failed');
    error.response = {
      status: 403,
      statusText: 'Forbidden',
      data: { detail: 'Access denied' },
      headers: {},
      config: { headers: new AxiosHeaders() },
    };

    expect(getApiErrorMessage(error)).toBe('Request failed');
  });
});

describe('axios.isAxiosError', () => {
  it('correctly identifies AxiosError', () => {
    const axiosError = new AxiosError('test');
    const regularError = new Error('test');

    expect(axios.isAxiosError(axiosError)).toBe(true);
    expect(axios.isAxiosError(regularError)).toBe(false);
  });
});
