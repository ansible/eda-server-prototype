/* eslint-disable no-unused-vars */
/**
 * These modules are not 100% accurate. It has to be fixed in FCE directly to provide 100% match.
 */

interface InternalAnyObject {
  [key: string]: any;
}

interface InternalStringObject {
  [key: string]: string;
}

declare enum SortByDirection {
  asc = 'asc',
  desc = 'desc'
}

interface InternalApiMetadata {
  count?: number;
  limit?: number;
  offset?: number;
}

type InternalAction = (type: string, ...args: any[]) => void;

interface InternalDispatch<A extends InternalAction> {
  <T extends A>(action: T): T;
}

interface PaginationConfiguration extends InternalApiMetadata {
  filter?: string;
  sortDirection?: SortByDirection;
}
interface ActionNotification {
  fulfilled?: InternalAnyObject;
  pending?: InternalAnyObject;
  rejected?: InternalAnyObject;
}

interface ActionMeta extends PaginationConfiguration, InternalAnyObject {
  storeState?: boolean;
  stateKey?: string;
  notifications?: ActionNotification;
  filters?: InternalStringObject;
  platformId?: string;
}
interface ReduxAction {
  type: string;
  payload?: any;
  meta: ActionMeta;
}

type ReducerHandler<T> = (state: T, action: ReduxAction) => T;
interface ReducerHandlerObject {
  [key: string]: ReducerHandler<any>;
}
type InternalReducerHash<T> = (
  reducerHash: ReducerHandlerObject,
  initialState: InternalAnyObject
) => ReducerHandler<T>;

interface NotificationConfig {
  variant: 'success' | 'info' | 'error';
  title: React.ReactNode;
  dismissable?: boolean;
  description?: React.ReactNode | React.ComponentType;
}

/**
 * Frontend components do not provide TS typings so we have to define them
 */
declare module '@redhat-cloud-services/frontend-components/DateFormat' {
  export interface DateFormatTooltipProps {
    [key: string]: number | string;
  }
  export interface DateFormatProps {
    date: Date | string | number | undefined;
    type?: 'exact' | 'onlyDate' | 'relative';
    extraTitle?: string;
    tooltipProps?: DateFormatTooltipProps;
    variant?: 'relative';
  }
  export const DateFormat: React.ComponentType<DateFormatProps>;
}

declare module '@redhat-cloud-services/frontend-components-utilities/ReducerRegistry' {
  export type ApplyReducerHash<T> = InternalReducerHash<T>;
  export function applyReducerHash<T>(
    reducer: ReducerHandlerObject,
    initialState: T
  ): ReducerHandler<T>;

  class ReducerRegistry {
    store: InternalAnyObject;
    constructor(
      initState?: InternalAnyObject,
      middlewares?: any[],
      composeEnhancersDefault?: (...args: any[]) => ReducerRegistry
    );
    getStore: () => InternalAnyObject;
    register(newReducers: ReducerHandlerObject): void;
  }

  export const reducerRegistry: ReducerRegistry;

  export default ReducerRegistry;
}

declare module '@redhat-cloud-services/frontend-components-notifications/redux' {
  const notificationsPrefix = '@@INSIGHTS-CORE/NOTIFICATIONS/';
  export const ADD_NOTIFICATION = `${notificationsPrefix}ADD_NOTIFICATION`;
  export const CLEAR_NOTIFICATIONS = `${notificationsPrefix}CLEAR_NOTIFICATIONS`;
  export type AddNotification = (
    notification: NotificationConfig
  ) => {
    type: string;
  };
  export const addNotification: AddNotification;
  export const clearNotifications: () => { type: string };
  export default clearNotifications;
}
declare module '@redhat-cloud-services/frontend-components-notifications/redux' {
  export function notificationsReducer<T>(): ReducerHandler<T>;
  export default notificationsReducer;
}

declare module '@redhat-cloud-services/frontend-components-notifications/notificationsMiddleware' {
  export interface NotificationsMiddlewareOptions {
    dispatchDefaultFailure?: boolean;
    pendingSuffix?: string;
    fulfilledSuffix?: string;
    rejectedSuffix?: string;
    autoDismiss?: boolean;
    dismissDelay?: number;
    errorTitleKey?: string[];
    errorDescriptionKey?: string[];
    useStatusText?: false;
  }

  type NotificationMiddleware = (
    store: InternalAnyObject
  ) => (
    next: InternalDispatch<any>
  ) => (action: InternalAction) => InternalAction;
  export const createNotificationsMiddleware: (
    options: NotificationsMiddlewareOptions
  ) => NotificationMiddleware;

  export default createNotificationsMiddleware;
}

declare module '@redhat-cloud-services/frontend-components/Section' {
  export const Section: React.ComponentType<any>;
}

declare module '@redhat-cloud-services/frontend-components/PrimaryToolbar' {
  interface TextInputProps {
    value?: string;
    placeholder?: string;
    onChange?: (
      event: React.SyntheticEvent<Element, Event>,
      value?: string
    ) => void;
  }

  interface Chip {
    name?: string;
    isRead?: boolean;
    count?: number;
    type?: string;
    chips?: Chip[];
  }

  type ActionsType = (
    | React.ReactNode
    | {
        label?: React.ReactNode;
        value?: number | string;
        onClick?: (...args: any[]) => void;
        props: { [key: string]: any };
      }
  )[];

  export interface ActiveFiltersConfig {
    className?: string;
    filters?:
      | { category: string; type?: string; chips: Chip | Chip[] }
      | { category: string; type?: string; chips: Chip | Chip[] }[]
      | Chip
      | Chip[];
    onDelete?: (
      event: React.MouseEvent<Element, MouseEvent>,
      chip: Chip[],
      clearAll?: boolean
    ) => void;
  }

  export interface FilterValues extends Omit<TextInputProps, 'onChange'> {
    id?: string;
    placeholder?: string;
    'aria-label'?: string;
    value?:
      | string
      | string[]
      | { label?: React.ReactNode; value?: string }
      | { [key: string]: any };
    onChange?: (
      event: React.SyntheticEvent<Element, Event>,
      value?: string
    ) => void;
    items?: { value: string; label: React.ReactNode }[];
  }

  export interface FilterItem {
    id?: string;
    label?: React.ReactNode;
    value?: string;
    type?: 'text' | 'checkbox' | 'radio' | 'custom' | 'group';
    filterValues: FilterValues | TextInputProps[];
    chips?: Chip[];
  }
  export interface FilterConfig {
    hideLabel?: boolean;
    items: FilterItem[];
    isDisabled?: boolean;
    value?: any;
    onChange?: (event: React.MouseEvent, value?: string) => void;
  }
  export interface PrimaryToolbarProps extends TextInputProps {
    dedicatedAction?: React.ReactNode;
    pagination?: { [key: string]: any };
    sortByConfig?: {
      direction: SortByDirection;
      onSortChange: (
        event: React.MouseEvent<HTMLButtonElement, MouseEvent>,
        direction: SortByDirection
      ) => void;
    };
    activeFiltersConfig?: ActiveFiltersConfig;
    filterConfig?: FilterConfig;
    className?: string;
    bulkSelect?: {
      count?: number;
      className?: string;
      items?: {
        title?: string;
        onClick?: (
          event: React.MouseEvent<any> | React.KeyboardEvent | MouseEvent,
          item: any,
          key: number
        ) => void;
      }[];
      checked?: boolean;
      id?: string;
      onSelect?: (
        checked: boolean,
        event: React.FormEvent<HTMLInputElement>
      ) => void;
      toggleProps?: { [key: string]: any };
    };
    toggleIsExpanded?: () => void;
    id?: string | number;
    actionsConfig?: {
      actions?: ActionsType;
      dropdownProps?: { [key: string]: any };
      onSelect?: (...args: any[]) => void;
    };
  }
  export const PrimaryToolbar: React.ComponentType<PrimaryToolbarProps>;
}

declare module '@redhat-cloud-services/frontend-components/TableToolbar' {
  export interface TableToolbarProps {
    className?: string;
  }
  export const TableToolbar: React.ComponentType<TableToolbarProps>;
}
