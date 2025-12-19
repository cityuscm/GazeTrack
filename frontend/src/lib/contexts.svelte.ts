import { Context } from "runed";

export const availableScenes = new Context<{[key: string]: string}>("availableScenes");
export const currentScene = new Context<string>("currentScene");
export const availableClients = new Context<{[key: string]: string}>("availableClients");
export const currentClients = new Context<string[]>("currentClients");
export const currentPage = new Context<string>("currentPage");