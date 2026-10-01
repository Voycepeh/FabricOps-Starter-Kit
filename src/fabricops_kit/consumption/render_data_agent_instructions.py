"""Render native Microsoft Fabric Data Agent instructions."""

from typing import Any, Mapping

from .shared import instruction_text


def render_data_agent_instructions(consumer_context: Mapping[str, Any]) -> dict[str, str]:
    """Render deterministic instructions for one table's Data Agent configuration.

    Parameters
    ----------
    consumer_context : mapping
        Context returned by :func:`build_consumer_context`.

    Returns
    -------
    dict[str, str]
        Separate ``agent`` and ``datasource`` instruction strings.

    Raises
    ------
    KeyError
        If required source context is absent.

    Notes
    -----
    Rendering is deterministic and invokes no AI service. The output contains no
    tokens, credentials, or profile sample values.

    Examples
    --------
    >>> instructions = render_data_agent_instructions({"source": {"table": "orders", "schema": "dbo"}, "columns": []})
    >>> "dbo.orders" in instructions["datasource"]
    True

    See Also
    --------
    build_consumer_context
    create_data_agent

    """
    return instruction_text(consumer_context)


__all__ = ["render_data_agent_instructions"]
