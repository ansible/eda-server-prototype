import React from 'react';
import { CodeEditor, Language } from '@patternfly/react-code-editor';
import useResizeObserver from '@react-hook/resize-observer';
import { debounce } from 'lodash';
import 'monaco-editor/esm/vs/basic-languages/yaml/yaml.contribution.js';
import 'monaco-editor/esm/vs/editor/editor.all.js';
import { useCallback, useEffect, useRef } from 'react';
import './EdaCodeEditor.css';

/**
 *
 * @param props
 */

export const EdaCodeEditor = (props: {
  code: any;
  editMode: boolean;
  width: string;
  height?: string;
  language: Language;
  setEditedCode?: React.Dispatch<React.SetStateAction<string>>;
  defaultScrollToLine?: number;
}) => {
  const { code, editMode, setEditedCode, width, height, language, defaultScrollToLine } = props;
  const pageRef = useRef(null);
  const editorRef = useRef<any | null>(null);
  const monacoRef = useRef<any | null>(null);

  useResizeObserver(pageRef, (entry) => {
    const { width } = entry.contentRect;
    const { height } = entry.contentRect;
    editorRef?.current?.layout({ width, height });
  });
  useEffect(() => {
    if (code && defaultScrollToLine) {
      editorRef.current?.revealLineNearTop(defaultScrollToLine);
    }
  }, [code, editorRef, defaultScrollToLine]);

  function onEditorDidMount(editor: any, monaco: any) {
    editorRef.current = editor;
    monacoRef.current = monaco;
  }

  // react to changes from editing yaml
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const onChange = useCallback(
    debounce((value) => {
      setEditedCode && setEditedCode(value);
    }, 100),
    []
  );

  return (
    <CodeEditor
      width={width}
      height={height ?? '100%'}
      code={code}
      onChange={onChange}
      language={language}
      onEditorDidMount={onEditorDidMount}
      isReadOnly={!editMode}
      isLineNumbersVisible={true}
      isMinimapVisible={false}
      options={{
        wordWrap: 'wordWrapColumn',
        wordWrapColumn: 132,
        scrollBeyondLastLine: true,
        smoothScrolling: true,
        glyphMargin: true,
        tabSize: 2,
      }}
    />
  );
};
