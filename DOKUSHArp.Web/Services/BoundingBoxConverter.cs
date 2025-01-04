using System.Text.Json;
using System.Text.Json.Serialization;

namespace DOKUSHArp.Web.Services;

public sealed class BoundingBoxConverter : JsonConverter<BoundingBox>
{
	public override BoundingBox Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
	{
		if (!TryAccept(ref reader, JsonTokenType.StartArray)) return default;

		if (!TryGetDouble(ref reader, out var x)) return default;

		if (!TryGetDouble(ref reader, out var y)) return default;

		if (!TryGetDouble(ref reader, out var width)) return default;

		if (!TryGetDouble(ref reader, out var height)) return default;

		return TryAccept(ref reader, JsonTokenType.EndArray, read: false) ? new BoundingBox(x, y, width, height) : default;
	}

	public override void Write(Utf8JsonWriter writer, BoundingBox value, JsonSerializerOptions options)
	{
		writer.WriteStartArray();
		writer.WriteNumberValue(value.X);
		writer.WriteNumberValue(value.Y);
		writer.WriteNumberValue(value.Width);
		writer.WriteNumberValue(value.Height);
		writer.WriteEndArray();
	}

	private static bool TryAccept(ref Utf8JsonReader reader, JsonTokenType acceptedToken, bool read = true)
	{
		if (reader.TokenType != acceptedToken) return false;

		if (read) reader.Read();

		return true;
	}

	private static bool TryGetDouble(ref Utf8JsonReader reader, out double value)
	{
		if (reader.TokenType != JsonTokenType.Number || !reader.TryGetDouble(out value))
		{
			value = default;

			return false;
		}

		reader.Read();

		return true;
	}
}