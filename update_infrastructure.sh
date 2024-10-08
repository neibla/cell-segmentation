#!/bin/bash
terraform -chdir=infrastructure init && terraform -chdir=infrastructure plan -out=tfplan && terraform -chdir=infrastructure apply tfplan                            
