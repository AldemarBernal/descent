using UnityEngine;
using System;
using System.Collections.Generic;

public class DescentModel
{
	public const int IDTA_EOF = 0;
	public const int IDTA_DEFPOINTS = 1;
	public const int IDTA_FLATPOLY = 2;
	public const int IDTA_TMAPPOLY = 3;
	public const int IDTA_SORTNORM = 4;
	public const int IDTA_RODBM = 5;
	public const int IDTA_SUBCALL = 6;
	public const int IDTA_DEFP_START = 7;
	public const int IDTA_GLOW = 8;

	public List<Vector3> vertices = new List<Vector3>();
	public List<int> triangles = new List<int>();
	public List<int> lines = new List<int>();
	public List<Vector2> uvs = new List<Vector2>();
	public int numModels = 0;

	public DescentModel(string filename) {
		TextAsset json = Resources.Load(filename) as TextAsset;
		JSONObject jsonModel = new JSONObject(json.text);

		Vector3[] offsets = GetOffsets(jsonModel);
		int[] parents = GetParents(jsonModel);
		Vector3 offset;

		numModels = int.Parse(jsonModel["num_models"].ToString());
		int currentModel = 0;
		while (currentModel < numModels) {
			offset = GetOffset (currentModel, offsets, parents);
			GetVertices(jsonModel["model_data"][currentModel.ToString()], offset);
			GetTriangles(jsonModel["model_data"][currentModel.ToString()]);
			GetUVs(jsonModel["model_data"][currentModel.ToString()]);

			currentModel++;
		}
	}

	Vector3[] GetOffsets(JSONObject model) {
		float x;
		float y;
		float z;
		int index = 0;
	
		Vector3[] offsets = new Vector3[10];

		foreach (JSONObject offset in model["submodel"]["offsets"].list) {
			x = float.Parse (offset["x"].ToString ()) / 65536;
			y = float.Parse (offset["y"].ToString ()) / 65536;
			z = float.Parse (offset["z"].ToString ()) / 65536;

			offsets[index++] = new Vector3 (x, y, z);
		}

		return offsets;
	}

	Vector3 GetOffset(int index, Vector3[] offsets, int[] parents) {
		Vector3 offset = new Vector3 ();

		if (parents [index] == 255) {
			offset = offsets [0];
		} else {
			offset = offsets [index];
			offset += GetOffset (parents [index], offsets, parents);
		}

		return offset;
	}

	int[] GetParents(JSONObject model) {
		int index = 0;

		int[] parents = new int[10];

		foreach (JSONObject offset in model["submodel"]["parents"].list) {
			parents [index++] = int.Parse (offset.ToString ());
		}

		return parents;
	}

	void GetVertices(JSONObject model, Vector3 offset) {
		float x;
		float y;
		float z;
		Vector3 vertex;

		foreach (JSONObject md in model.list) {
			
			switch (int.Parse(md["idta"].ToString ())) {
				case IDTA_SORTNORM:
					GetVertices(md["z_front_nodes"], offset);
					GetVertices(md["z_back_nodes"], offset);
					break;

				case IDTA_SUBCALL:
					GetVertices(md["subcall"], offset);
					break;

				case IDTA_DEFP_START:
					foreach (JSONObject v in md["vms_points"].list) {
						x = float.Parse(v["x"].ToString()) / 65536;
						y = float.Parse(v["y"].ToString()) / 65536;
						z = float.Parse(v["z"].ToString()) / 65536;

						vertex = new Vector3 (x, y, z);
						vertex += offset;

						vertices.Add(vertex);
					}
					break;
			
			}
		}
	}

	void GetTriangles(JSONObject model) {
		int t1;
		int t2;
		int t3;
		int numPoints;

		foreach (JSONObject md in model.list) {

			switch (int.Parse(md["idta"].ToString ())) {

				case IDTA_FLATPOLY:
				case IDTA_TMAPPOLY:
					numPoints = int.Parse (md ["num_points"].ToString ());

					for (t1 = 0; t1 < numPoints; t1++) {
						for (t2 = 1; t2 < numPoints; t2++) {
							for (t3 = 2; t3 < numPoints; t3++) {
								if (t1 != t2 && t1 != t3 && t2 != t3) {
									if (t1 < t2 && t2 < t3) {
										triangles.Add (int.Parse (md ["pltdx"] [t1].ToString ()));
										triangles.Add (int.Parse (md ["pltdx"] [t2].ToString ()));
										triangles.Add (int.Parse (md ["pltdx"] [t3].ToString ()));
									}
								}
							}
						}
					}

					break;

				case IDTA_SORTNORM:
					GetTriangles(md["z_front_nodes"]);
					GetTriangles(md["z_back_nodes"]);
					break;

				case IDTA_SUBCALL:
					GetTriangles(md["subcall"]);
					break;

			}
		}
	}

	void GetLines(JSONObject model) {
		foreach (JSONObject md in model.list) {

			switch (int.Parse(md["idta"].ToString ())) {

			case IDTA_FLATPOLY:
			case IDTA_TMAPPOLY:
				foreach (JSONObject line in md["pltdx"].list) {
					lines.Add (int.Parse (line.ToString ()));
				}
				break;

			case IDTA_SORTNORM:
				GetTriangles(md["z_front_nodes"]);
				GetTriangles(md["z_back_nodes"]);
				break;

			case IDTA_SUBCALL:
				GetTriangles(md["subcall"]);
				break;

			}
		}
	}

	void GetNormals(JSONObject model) {
		float x;
		float y;
		float z;
		Vector3 vertex;

		foreach (JSONObject md in model.list) {

			switch (int.Parse(md["idta"].ToString ())) {
			case IDTA_FLATPOLY:
			case IDTA_TMAPPOLY:
				foreach (JSONObject v in md["vms_points"].list) {
					x = float.Parse(v["x"].ToString()) / 65536;
					y = float.Parse(v["y"].ToString()) / 65536;
					z = float.Parse(v["z"].ToString()) / 65536;

//					vertex = new Vector3 (x, y, z);
//					vertex += offset;

//					vertices.Add(vertex);
				}
				break;

			case IDTA_SORTNORM:
				GetNormals(md["z_front_nodes"]);
				GetNormals(md["z_back_nodes"]);
				break;

			case IDTA_SUBCALL:
				GetNormals(md["subcall"]);
				break;

			}
		}
	}

	void GetUVs(JSONObject model) {
		for (int i = 0; i < vertices.Count; i++) {
			uvs.Add (new Vector2 (vertices [i].x / 3, vertices [i].z / 3));
		}
	}
}
