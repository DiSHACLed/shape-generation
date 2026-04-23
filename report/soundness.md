# excel tab

See the `violations` tab in the generated excel file;
`x / y` should be read as:
- `x` violations when validating the generated shapes against the input data & 
- `y` violations when validating the shapes as closed (overwritten with `sh:closed true` for every nodeshape; 
  see [rewrite query from shacl play](https://github.com/sparna-git/shacl-play/blob/master/shacl-validator/src/main/resources/fr/sparna/rdf/shacl/closeShapes/CloseShapes.rq)).

**Shexer's results should be rerun after the following bugs have resolved;**
TODO
TODO

# soundness

Given graph G and consider S its generated shape graph.
If validating G against S contains no validations, we will call S sound wrt. G.

Depending on the tool and the settings with which it is ran, we may expect generated shapes to be sound wrt the input graph from which they were generated.

# explanations of different variants of QSE / shexer

- qse($0\leq\phi\leq 1$):
  See def 2.5 (confidence) from their paper.
  Note though; *as I understand it* the parameter given as input for QSE does not immediately correspond to the notion of confidence as described in the paper.

  Candidate constraints will be taken into consideration if at least $\phi$ of all instances satisfy it; afterwards, the filtered constraints are merged (in a "logically consistent way").

  So $\phi = 0$ (taking into consideration) would not filter out any constraints; but after (logically consistent merging) you would end up with a sound (& very [precise](./precision.md)) shapes.
  With $\phi = 1$ (taking into consideration constraints which are always satisfied), we also expect no violations (but a bit less precise);
  though some fields may be missing now, so we would expect violations at $1$ when interpreting the shapes as closed.

  We may expect violations for any $\phi \neq 0, 1$.
  
  Note; qse also offers an absolute cutoff called support (see definition 2.4); for simplicity, we leave this at $0$.

- shexer($0\leq\phi\leq 1,bool$):
  TODO; revisit this when following bugs are solved.

# artificial tests (`people*.ttl`)

We consider the following test cases (`people-*.ttl`);
- 90% has birthday `xsd:date`, but 10% `xsd:datetime` (`people-datetime.ttl`)
- ..., 10% has string literal (`people-string.ttl`)
- 90% has `foaf:birthday` but 10% `schema:birthDate` (`people-foaf-schema.ttl`)
- 90% has one birthday `foaf:birthday`, but 10% has two (`people-two-birthday.ttl`)
- 90% has one birthday `foaf:birthday`, but 10% has none (`people-without-birthday.ttl`)
- 60% has one birthday `foaf:birthday` with `xsd:date`, but 40% have the above four quirks

# real datasets

TODO

# Coverage 

A more binary question is whether predicates from some typed subject always make the final shape;
this reduces to the question whether the shape is [sound](./sound.md) when interpreted as closed.