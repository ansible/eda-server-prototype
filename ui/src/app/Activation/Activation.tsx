import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import Ansi from "ansi-to-react";
import {
  Card,
  CardBody as PFCardBody,
  CardTitle,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import styled from 'styled-components';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://localhost:8000/activation/';

const Activation: React.FunctionComponent = () => {

  const [activation, setActivation] = useState([]);

  let { id } = useParams();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setActivation(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Activation {activation.name}</Title>
  </PageSection>
  <Link to={"/rule/" + activation.ruleset_id}>{activation.ruleset_name}</Link>
  <Link to={"/inventory/" + activation.inventory_id}>{activation.inventory_name}</Link>
  <Link to={"/var/" + activation.extravars_id}>{activation.extravars_name}</Link>
  </React.Fragment>
)
}

export { Activation };
