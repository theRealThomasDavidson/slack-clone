/// <reference types="jest" />

declare global {
  var global: typeof globalThis;
  var jest: any;
  var describe: jest.Describe;
  var it: jest.It;
  var expect: jest.Expect;
  var beforeEach: jest.Lifecycle;
  var afterEach: jest.Lifecycle;
  var beforeAll: jest.Lifecycle;
  var afterAll: jest.Lifecycle;
}

export {}; 